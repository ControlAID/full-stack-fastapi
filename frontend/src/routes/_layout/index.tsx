import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Building2, Key, Users, Activity, TrendingUp } from "lucide-react"

import { MonitoringService, UsersService, OrganizationsService, LicensesService } from "@/client"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - FastAPI Cloud",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  const { data: users } = useQuery({
    queryKey: ["users-count"],
    queryFn: () => UsersService.readUsers({ limit: 1 }),
  })

  const { data: organizations } = useQuery({
    queryKey: ["organizations-count"],
    queryFn: () => OrganizationsService.readOrganizations({ limit: 1 }),
  })

  const { data: licenses } = useQuery({
    queryKey: ["licenses-count"],
    queryFn: () => LicensesService.readLicenses({ limit: 1 }),
  })

  const { data: metrics } = useQuery({
    queryKey: ["monitoring-metrics"],
    queryFn: () => MonitoringService.getMetrics(),
    refetchInterval: 5000, // Refresh every 5 seconds
    enabled: currentUser?.is_superuser,
  })

  const stats = [
    {
      label: "Total Users",
      value: users?.count || 0,
      growth: metrics?.counts.users_growth,
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      label: "Organizations",
      value: organizations?.count || 0,
      growth: metrics?.counts.organizations_growth,
      icon: Building2,
      color: "text-emerald-600",
      bgColor: "bg-emerald-100",
    },
    {
      label: "Active Licenses",
      value: licenses?.count || 0,
      growth: metrics?.counts.licenses_growth,
      icon: Key,
      color: "text-amber-600",
      bgColor: "bg-amber-100",
    },
    {
      label: "CPU Usage",
      value: metrics ? `${metrics.cpu_usage.toFixed(1)}%` : "N/A",
      growth: 0, // No growth for CPU
      icon: Activity,
      color: "text-rose-600",
      bgColor: "bg-rose-100",
    },
  ]

  return (
    <div className="flex flex-col gap-8 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground text-lg">
          Welcome to your ControlAI command center. Here's what's happening today.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="group relative overflow-hidden rounded-2xl border bg-card p-6 transition-all hover:shadow-lg dark:hover:shadow-primary/10"
          >
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  {stat.label}
                </p>
                <p className="text-3xl font-bold">{stat.value}</p>
              </div>
              <div className={`${stat.bgColor} ${stat.color} rounded-xl p-3 transition-transform group-hover:scale-110`}>
                <stat.icon className="h-6 w-6" />
                <div className="absolute -right-2 -top-2 h-24 w-24 rounded-full bg-current opacity-5 blur-2xl group-hover:opacity-10" />
              </div>
            </div>
            <div className={`mt-4 flex items-center gap-2 text-xs font-semibold ${stat.growth && stat.growth >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              <TrendingUp className={`h-3 w-3 ${stat.growth && stat.growth < 0 ? 'rotate-180' : ''}`} />
              <span>{stat.growth !== undefined ? `${stat.growth >= 0 ? '+' : ''}${stat.growth.toFixed(1)}% from last month` : "N/A from last month"}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border bg-card p-6 shadow-sm">
          <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <button className="flex items-center gap-3 rounded-xl border p-4 text-left transition-colors hover:bg-accent group">
              <div className="rounded-lg bg-primary/10 p-2 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <Users className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold text-sm">Create User</p>
                <p className="text-xs text-muted-foreground">Add new system member</p>
              </div>
            </button>
            <button className="flex items-center gap-3 rounded-xl border p-4 text-left transition-colors hover:bg-accent group">
              <div className="rounded-lg bg-primary/10 p-2 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <Building2 className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold text-sm">New Org</p>
                <p className="text-xs text-muted-foreground">Setup tenant structure</p>
              </div>
            </button>
          </div>
        </div>

        <div className="rounded-2xl border bg-card p-6 shadow-sm overflow-hidden relative">
          <div className="absolute right-0 top-0 h-full w-48 bg-linear-to-l from-primary/5 to-transparent -z-1" />
          <h3 className="text-xl font-bold mb-2">System Status</h3>
          <p className="text-muted-foreground mb-6">Real-time health monitoring.</p>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Database Status</span>
              <span className={`font-medium ${metrics?.db_status === 'stable' ? 'text-emerald-600' : 'text-rose-600'}`}>
                {metrics?.db_status || "Checking..."}
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-secondary">
              <div
                className={`h-full rounded-full transition-all duration-500 ${metrics?.db_status === 'stable' ? 'bg-emerald-500' : 'bg-rose-500'}`}
                style={{ width: metrics?.db_status === 'stable' ? '100%' : '0%' }}
              />
            </div>
            <div className="flex items-center justify-between text-sm pt-2">
              <span className="text-muted-foreground">Memory Usage</span>
              <span className="font-medium text-blue-600">{metrics ? `${metrics.memory_usage.toFixed(1)}%` : "N/A"}</span>
            </div>
            <div className="h-2 w-full rounded-full bg-secondary">
              <div
                className="h-full bg-blue-500 rounded-full shadow-sm shadow-blue-500/50 transition-all duration-500"
                style={{ width: metrics ? `${metrics.memory_usage}%` : '0%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
