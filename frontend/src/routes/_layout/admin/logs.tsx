import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense, useState } from "react"
import { ScrollText, Search, X } from "lucide-react"

import { type LogPublic, MonitoringService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import type { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { LogDetails } from "@/components/Logs/LogDetails"

function getLogsQueryOptions(level?: string, target?: string) {
  return {
    queryFn: () => MonitoringService.getLogs({
      skip: 0,
      limit: 100,
      level: level === "all" ? undefined : level,
      target: target || undefined
    }),
    queryKey: ["audit-logs", level, target],
  }
}

export const Route = createFileRoute("/_layout/admin/logs")({
  component: AdminLogs,
})

const columns: ColumnDef<LogPublic>[] = [
  {
    accessorKey: "timestamp",
    header: "Timestamp",
    cell: ({ row }) => new Date(row.original.timestamp).toLocaleString(),
  },
  {
    accessorKey: "level",
    header: "Level",
    cell: ({ row }) => {
      const level = row.original.level
      let variant: "default" | "secondary" | "destructive" | "outline" | "success" = "secondary"

      switch (level) {
        case "error": variant = "destructive"; break;
        case "warning": variant = "outline"; break;
        case "success": variant = "success"; break;
        case "info": variant = "secondary"; break;
      }

      return <Badge variant={variant} className="capitalize">{level}</Badge>
    }
  },
  {
    accessorKey: "action",
    header: "Action",
    cell: ({ row }) => <span className="font-medium">{row.original.action}</span>,
  },
  {
    accessorKey: "target",
    header: "Target",
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <LogDetails log={row.original} />
      </div>
    )
  }
]

function LogsTableContent({ level, target }: { level: string, target: string }) {
  const { data } = useSuspenseQuery(getLogsQueryOptions(level, target))
  return <DataTable columns={columns} data={data.data || []} />
}

function AdminLogs() {
  const [level, setLevel] = useState<string>("all")
  const [target, setTarget] = useState<string>("")
  const [searchInput, setSearchInput] = useState<string>("")

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setTarget(searchInput)
  }

  const clearFilters = () => {
    setLevel("all")
    setTarget("")
    setSearchInput("")
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <ScrollText className="h-6 w-6" />
            Audit Logs
          </h1>
          <p className="text-muted-foreground">
            Track all administrative actions across the system
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search target..."
              className="pl-8 w-[200px]"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
          </form>

          <Select value={level} onValueChange={setLevel}>
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="Level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              <SelectItem value="info">Info</SelectItem>
              <SelectItem value="success">Success</SelectItem>
              <SelectItem value="warning">Warning</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>

          {(level !== "all" || target !== "") && (
            <Button variant="ghost" size="sm" onClick={clearFilters} className="h-9">
              <X className="mr-2 h-4 w-4" />
              Reset
            </Button>
          )}
        </div>
      </div>

      <Suspense fallback={<div>Loading logs...</div>}>
        <LogsTableContent level={level} target={target} />
      </Suspense>
    </div>
  )
}
