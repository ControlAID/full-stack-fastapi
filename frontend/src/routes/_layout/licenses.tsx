import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"

import { LicensesService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers" // Reusing generic loader

// Will create next
import { columns } from "@/components/Licenses/columns"
import AddLicense from "@/components/Licenses/AddLicense"

function getLicensesQueryOptions() {
  return {
    queryFn: () => LicensesService.readLicenses({ skip: 0, limit: 100 }),
    queryKey: ["licenses"],
  }
}

export const Route = createFileRoute("/_layout/licenses")({
  component: Licenses,
  head: () => ({
    meta: [
      {
        title: "Licenses - FastAPI Cloud",
      },
    ],
  }),
})

function LicensesTableContent() {
  const { data: licenses } = useSuspenseQuery(getLicensesQueryOptions())

  return <DataTable columns={columns} data={licenses.data} />
}

function LicensesTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <LicensesTableContent />
    </Suspense>
  )
}

function Licenses() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Licenses</h1>
          <p className="text-muted-foreground">
            Manage organization licenses and limits
          </p>
        </div>
        <AddLicense />
      </div>
      <LicensesTable />
    </div>
  )
}
