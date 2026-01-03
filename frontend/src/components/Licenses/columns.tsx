import type { ColumnDef } from "@tanstack/react-table"

import type { LicensePublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { LicenseActionsMenu } from "./LicenseActionsMenu"

export const columns: ColumnDef<LicensePublic>[] = [
    {
        accessorKey: "license_key",
        header: "License Key",
        cell: ({ row }) => (
            <span className="font-mono text-xs">{row.original.license_key}</span>
        ),
    },
    {
        accessorKey: "tier",
        header: "Type",
        cell: ({ row }) => {
            const tier = row.original.tier
            let variant: "default" | "secondary" | "destructive" | "outline" = "outline"

            switch (tier) {
                case "starter": variant = "secondary"; break;
                case "business": variant = "default"; break;
                case "enterprise": variant = "destructive"; break; // Just to make it pop
            }

            return <Badge variant={variant} className="capitalize">{tier}</Badge>
        },
    },
    {
        accessorKey: "is_active",
        header: "Status",
        cell: ({ row }) => {
            const isActive = row.original.is_active
            return (
                <div className="flex items-center gap-2">
                    <span
                        className={cn(
                            "size-2 rounded-full",
                            isActive ? "bg-green-500" : "bg-red-500",
                        )}
                    />
                    <span className="capitalize">{isActive ? "Active" : "Inactive"}</span>
                </div>
            )
        },
    },
    {
        accessorKey: "valid_until",
        header: "Expires",
        cell: ({ row }) => {
            const date = row.original.valid_until
            return date ? new Date(date).toLocaleDateString() : "Never"
        },
    },
    {
        id: "actions",
        header: () => <span className="sr-only">Actions</span>,
        cell: ({ row }) => (
            <div className="flex justify-end">
                <LicenseActionsMenu license={row.original} />
            </div>
        ),
    },
]
