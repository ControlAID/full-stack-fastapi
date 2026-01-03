import type { ColumnDef } from "@tanstack/react-table"

import type { OrganizationUnitPublic } from "@/client"
import { Badge } from "@/components/ui/badge"

export const columns: ColumnDef<OrganizationUnitPublic>[] = [
    {
        accessorKey: "name",
        header: "Name",
        cell: ({ row }) => (
            <span className="font-medium">{row.original.name}</span>
        ),
    },
    {
        accessorKey: "type",
        header: "Type",
        cell: ({ row }) => (
            <Badge variant="outline">
                {row.original.type}
            </Badge>
        ),
    },
    {
        accessorKey: "related_unit_id",
        header: "Linked From/To",
        cell: ({ row }) => (
            <span className="text-muted-foreground text-xs">
                {row.original.related_unit_id || "-"}
            </span>
        ),
        // Ideally we would resolve the name of the related unit, but we only have ID in the public model row usually.
        // If we want names, we did not add related_unit_name to OrganizationUnitPublic in backend models.
        // We can fetch it or just show ID for now, or update backend model again.
        // Given scope, I'll show ID or just "-" if null.
    },
]
