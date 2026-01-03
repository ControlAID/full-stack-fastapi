import type { ColumnDef } from "@tanstack/react-table"

import type { OrganizationPublic } from "@/client"
import { cn } from "@/lib/utils"
// Will create this next
import { OrganizationActionsMenu } from "./OrganizationActionsMenu"

export const columns: ColumnDef<OrganizationPublic>[] = [
    {
        accessorKey: "name",
        header: "Name",
        cell: ({ row }) => (
            <span className="font-medium">{row.original.name}</span>
        ),
    },
    {
        accessorKey: "contact_email",
        header: "Contact Email",
        cell: ({ row }) => (
            <span className="text-muted-foreground">{row.original.contact_email || "N/A"}</span>
        ),
    },
    {
        accessorKey: "is_active",
        header: "Status",
        cell: ({ row }) => (
            <div className="flex items-center gap-2">
                <span
                    className={cn(
                        "size-2 rounded-full",
                        row.original.is_active ? "bg-green-500" : "bg-gray-400",
                    )}
                />
                <span className={row.original.is_active ? "" : "text-muted-foreground"}>
                    {row.original.is_active ? "Active" : "Inactive"}
                </span>
            </div>
        ),
    },
    {
        id: "actions",
        header: () => <span className="sr-only">Actions</span>,
        cell: ({ row }) => (
            <div className="flex justify-end">
                <OrganizationActionsMenu organization={row.original} />
            </div>
        ),
    },
]
