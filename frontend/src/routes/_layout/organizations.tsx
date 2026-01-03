import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Suspense } from "react"

import { OrganizationsService, UsersService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers" // Reusing generic pending loader for now

// Placeholder for columns, will create next
import { columns } from "@/components/Organizations/columns"
import AddOrganization from "@/components/Organizations/AddOrganization"

function getOrganizationsQueryOptions() {
  return {
    queryFn: () => OrganizationsService.readOrganizations({ skip: 0, limit: 100 }),
    queryKey: ["organizations"],
  }
}

export const Route = createFileRoute("/_layout/organizations")({
  component: Organizations,
  beforeLoad: async ({ context }) => {
    const queryClient = context.queryClient
    try {
      const user = await queryClient.ensureQueryData({
        queryKey: ["currentUser"],
        queryFn: UsersService.readUserMe,
      })
      if (!user.is_superuser) {
        throw redirect({
          to: "/",
        })
      }
    } catch (e) {
      throw redirect({
        to: "/login",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Organizations - FastAPI Cloud",
      },
    ],
  }),
})

function OrganizationsTableContent() {
  const { data: organizations } = useSuspenseQuery(getOrganizationsQueryOptions())

  return <DataTable columns={columns} data={organizations.data} />
}

function OrganizationsTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <OrganizationsTableContent />
    </Suspense>
  )
}

function Organizations() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Organizations</h1>
          <p className="text-muted-foreground">
            Manage customer organizations and their details
          </p>
        </div>
        <AddOrganization />
      </div>
      <OrganizationsTable />
    </div>
  )
}
