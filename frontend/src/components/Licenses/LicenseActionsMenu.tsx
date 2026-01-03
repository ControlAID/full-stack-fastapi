import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { LicensePublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteLicense from "./DeleteLicense"
import EditLicense from "./EditLicense"

interface LicenseActionsMenuProps {
    license: LicensePublic
}

export const LicenseActionsMenu = ({ license }: LicenseActionsMenuProps) => {
    const [open, setOpen] = useState(false)

    return (
        <DropdownMenu open={open} onOpenChange={setOpen}>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                    <EllipsisVertical />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <EditLicense license={license} onSuccess={() => setOpen(false)} />
                <DeleteLicense id={license.id} onSuccess={() => setOpen(false)} />
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
