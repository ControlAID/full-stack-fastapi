import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type LicenseCreate, LicensesService, OrganizationsService, MonitoringService, type ModulePublic } from "@/client"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
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
    license_key: z.string().optional(),
    tier: z.enum(["starter", "business", "enterprise"]),
    organization_id: z.string().uuid({ message: "Organization is required" }),
    is_active: z.boolean(),
    max_users: z.number().min(1),
    max_locations: z.number().min(1),
    max_devices: z.number().min(1),
    valid_until: z.string().min(1, { message: "Expiration date is required" }),
    addon_modules: z.array(z.string()),
})

type FormData = z.infer<typeof formSchema>

const AddLicense = () => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()

    // Fetch organizations for the select dropdown
    const { data: organizationsData } = useQuery({
        queryKey: ["organizations"],
        queryFn: () => OrganizationsService.readOrganizations({ skip: 0, limit: 100 }),
        enabled: isOpen, // Only fetch when dialog opens
    })

    // Fetch available modules/plugins
    const { data: modulesData } = useQuery({
        queryKey: ["modules"],
        queryFn: () => MonitoringService.getModules(),
        enabled: isOpen,
    })

    const form = useForm<FormData>({
        resolver: zodResolver(formSchema),
        mode: "onBlur",
        defaultValues: {
            license_key: "",
            tier: "starter",
            organization_id: "",
            is_active: true,
            max_users: 10,
            max_locations: 1,
            max_devices: 5,
            valid_until: new Date(
                new Date().setFullYear(new Date().getFullYear() + 1),
            ).toISOString().split('T')[0],
            addon_modules: [],
        },
    })

    const mutation = useMutation({
        mutationFn: (data: LicenseCreate) =>
            LicensesService.createLicense({ requestBody: data }),
        onSuccess: () => {
            showSuccessToast("License created successfully")
            form.reset()
            setIsOpen(false)
        },
        onError: handleError.bind(showErrorToast),
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["licenses"] })
        },
    })

    const onSubmit = (data: FormData) => {
        mutation.mutate({
            ...data,
            valid_from: new Date().toISOString(),
            valid_until: new Date(data.valid_until).toISOString(),
        })
    }

    return (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
                <Button className="my-4">
                    <Plus className="mr-2" />
                    Add License
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Add License</DialogTitle>
                    <DialogDescription>
                        Create a new license and assign it to an organization.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)}>
                        <div className="grid gap-4 py-4">
                            <FormField
                                control={form.control}
                                name="organization_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Organization</FormLabel>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select an organization" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {organizationsData?.data.map((org) => (
                                                    <SelectItem key={org.id} value={org.id}>
                                                        {org.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="license_key"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>
                                            License Key <span className="text-muted-foreground text-xs font-normal ml-2">(leave empty for auto-generation)</span>
                                        </FormLabel>
                                        <FormControl>
                                            <Input placeholder="XXXX-XXXX-XXXX-XXXX" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="tier"
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
                                                <SelectItem value="starter">Starter</SelectItem>
                                                <SelectItem value="business">Business</SelectItem>
                                                <SelectItem value="enterprise">Enterprise</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <div className="grid grid-cols-3 gap-2">
                                <FormField
                                    control={form.control}
                                    name="max_users"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Max Users</FormLabel>
                                            <FormControl>
                                                <Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="max_locations"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Max Locs</FormLabel>
                                            <FormControl>
                                                <Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="max_devices"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Max Devs</FormLabel>
                                            <FormControl>
                                                <Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </div>

                            <FormField
                                control={form.control}
                                name="valid_until"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Expiration Date</FormLabel>
                                        <FormControl>
                                            <Input type="date" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="addon_modules"
                                render={() => (
                                    <FormItem>
                                        <div className="mb-4">
                                            <FormLabel className="text-base">Modules Access</FormLabel>
                                        </div>
                                        <div className="flex flex-wrap gap-4">
                                            {modulesData?.data.map((module: ModulePublic) => (
                                                <FormField
                                                    key={module.name}
                                                    control={form.control}
                                                    name="addon_modules"
                                                    render={({ field }) => {
                                                        return (
                                                            <FormItem
                                                                key={module.name}
                                                                className="flex flex-row items-center space-x-3 space-y-0"
                                                            >
                                                                <FormControl>
                                                                    <Checkbox
                                                                        checked={field.value?.includes(module.name)}
                                                                        onCheckedChange={(checked) => {
                                                                            return checked
                                                                                ? field.onChange([...field.value, module.name])
                                                                                : field.onChange(
                                                                                    field.value?.filter(
                                                                                        (value) => value !== module.name,
                                                                                    ),
                                                                                )
                                                                        }}
                                                                    />
                                                                </FormControl>
                                                                <FormLabel className="font-normal">
                                                                    {module.name}
                                                                </FormLabel>
                                                            </FormItem>
                                                        )
                                                    }}
                                                />
                                            ))}
                                        </div>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="is_active"
                                render={({ field }) => (
                                    <FormItem className="flex items-center gap-3 space-y-0">
                                        <FormControl>
                                            <Checkbox
                                                checked={field.value}
                                                onCheckedChange={field.onChange}
                                            />
                                        </FormControl>
                                        <FormLabel className="font-normal">Is active?</FormLabel>
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

export default AddLicense
