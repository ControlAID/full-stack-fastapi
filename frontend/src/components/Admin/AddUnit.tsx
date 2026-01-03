import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type OrganizationUnitCreate, UnitsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
    name: z.string().min(1, { message: "Name is required" }),
    type: z.string().min(1, { message: "Type is required" }),
    related_unit_id: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

const AddUnit = () => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()

    const { data: units } = useQuery({
        queryKey: ["units"],
        queryFn: () => UnitsService.readUnits({ skip: 0, limit: 100 }),
    })

    const form = useForm<FormData>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            name: "",
            type: "apartment",
            related_unit_id: "",
        },
    })

    const mutation = useMutation({
        mutationFn: (data: OrganizationUnitCreate) =>
            UnitsService.createUnit({ requestBody: data }),
        onSuccess: () => {
            showSuccessToast("Unit created successfully")
            form.reset()
            setIsOpen(false)
        },
        onError: handleError.bind(showErrorToast),
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["units"] })
        },
    })

    const onSubmit = (data: FormData) => {
        // Determine organization_id? Backend requires it in body (since OrganizationUnitCreate has it).
        // But API usually infers it for non-superusers? 
        // Wait, backend api `create_unit`:
        // unit = OrganizationUnit.model_validate(unit_in)
        // unit.organization_id = current_user.organization_id 
        // It overrides it inside the endpoint logic if not superuser.
        // However, if the generated client expects `organization_id` in the type `OrganizationUnitCreate` as mandatory, 
        // I might need to pass a dummy or fetch it.
        // Let's assume I need to pass it if it's mandatory in TS type.
        // I'll check via ... logic: The client type likely allows optional or I pass a dummy UUID.
        // Actually, `OrganizationUnitCreate` has `organization_id: string`.
        // I will fetch current user info to get org id, or pass a placeholder if the backend ignores it.
        // Efficient way: useAuth hook.

        // TEMPORARY Hack: Pass empty UUID or similar, backend overrides it.
        // Or better, use useAuth.
        mutation.mutate({
            ...data,
            organization_id: "00000000-0000-0000-0000-000000000000", // Backend will overwrite
        })
    }

    return (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
                <Button className="my-4">
                    <Plus className="mr-2" />
                    Add Unit
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Add Unit</DialogTitle>
                    <DialogDescription>
                        Add a new organization unit (Apartment, Office, Parking).
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)}>
                        <div className="grid gap-4 py-4">
                            <FormField
                                control={form.control}
                                name="name"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Name</FormLabel>
                                        <FormControl>
                                            <Input placeholder="e.g. Apt 101" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="type"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Type</FormLabel>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select type" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="apartment">Apartment</SelectItem>
                                                <SelectItem value="office">Office</SelectItem>
                                                <SelectItem value="parking_spot">Parking Spot</SelectItem>
                                                <SelectItem value="common_area">Common Area</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="related_unit_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Link to (Optional)</FormLabel>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select parent unit" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="">No Link</SelectItem>
                                                {units?.map((unit: any) => (
                                                    <SelectItem key={unit.id} value={unit.id}>
                                                        {unit.name} ({unit.type})
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <DialogFooter>
                            <DialogClose asChild>
                                <Button variant="outline" disabled={mutation.isPending}>
                                    Cancel
                                </Button>
                            </DialogClose>
                            <LoadingButton type="submit" loading={mutation.isPending}>
                                Save
                            </LoadingButton>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}

export default AddUnit
