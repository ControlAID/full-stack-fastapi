import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"

import { LicensesService } from "@/client"
import { Button } from "@/components/ui/button"
import {
    AlertDialog,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface DeleteLicenseProps {
    id: string
    onSuccess: () => void
}

const DeleteLicense = ({ id, onSuccess }: DeleteLicenseProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()

    const mutation = useMutation({
        mutationFn: () => LicensesService.deleteLicense({ licenseId: id }),
        onSuccess: () => {
            showSuccessToast("License deleted successfully")
            setIsOpen(false)
            onSuccess()
        },
        onError: handleError.bind(showErrorToast),
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["licenses"] })
        },
    })

    return (
        <AlertDialog open={isOpen} onOpenChange={setIsOpen}>
            <DropdownMenuItem
                variant="destructive"
                onSelect={(e) => e.preventDefault()}
                onClick={() => setIsOpen(true)}
            >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete License
            </DropdownMenuItem>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete the license.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={mutation.isPending}>Cancel</AlertDialogCancel>
                    <Button
                        variant="destructive"
                        onClick={() => mutation.mutate()}
                        disabled={mutation.isPending}
                    >
                        {mutation.isPending ? "Deleting..." : "Delete"}
                    </Button>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}

export default DeleteLicense
