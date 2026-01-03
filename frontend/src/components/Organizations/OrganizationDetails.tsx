import { useQuery } from "@tanstack/react-query"
import { Building2, Key, Users, Info, ShieldCheck } from "lucide-react"
import { useState } from "react"

import { type OrganizationPublic, OrganizationsService } from "@/client"
import { Badge } from "@/components/ui/badge"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface OrganizationDetailsProps {
    organization: OrganizationPublic
}

const OrganizationDetails = ({ organization }: OrganizationDetailsProps) => {
    const [isOpen, setIsOpen] = useState(false)

    const { data: usersData, isLoading: usersLoading } = useQuery({
        queryKey: ["organization-users", organization.id],
        queryFn: () => OrganizationsService.readOrganizationUsers({ organizationId: organization.id }),
        enabled: isOpen,
    })

    const { data: licensesData, isLoading: licensesLoading } = useQuery({
        queryKey: ["organization-licenses", organization.id],
        queryFn: () => OrganizationsService.readOrganizationLicenses({ organizationId: organization.id }),
        enabled: isOpen,
    })

    return (
        <>
            <DropdownMenuItem
                onSelect={(e) => e.preventDefault()}
                onClick={() => setIsOpen(true)}
            >
                <Info className="mr-2 h-4 w-4" />
                View Details
            </DropdownMenuItem>

            <Dialog open={isOpen} onOpenChange={setIsOpen}>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <div className="flex items-center gap-2">
                            <Building2 className="h-6 w-6 text-primary" />
                            <DialogTitle className="text-2xl font-bold">{organization.name}</DialogTitle>
                        </div>
                        <DialogDescription>
                            Detailed information and management for {organization.name}
                        </DialogDescription>
                    </DialogHeader>

                    <Tabs defaultValue="overview" className="w-full mt-4">
                        <TabsList className="grid w-full grid-cols-3">
                            <TabsTrigger value="overview">Overview</TabsTrigger>
                            <TabsTrigger value="users">Users ({usersData?.count || 0})</TabsTrigger>
                            <TabsTrigger value="license">License</TabsTrigger>
                        </TabsList>

                        <TabsContent value="overview" className="space-y-4 mt-4">
                            <div className="grid gap-4 md:grid-cols-2">
                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                                            <Info className="h-4 w-4" /> General Info
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-1 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Type:</span>
                                            <span className="font-semibold capitalize">{organization.type}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Email:</span>
                                            <span className="font-semibold">{organization.contact_email}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Status:</span>
                                            <Badge variant={organization.is_active ? "success" : "destructive"}>
                                                {organization.is_active ? "Active" : "Inactive"}
                                            </Badge>
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader className="pb-2">
                                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                                            <ShieldCheck className="h-4 w-4" /> Infrastructure
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-1 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Database:</span>
                                            <code className="bg-secondary px-1 rounded text-xs">{organization.db_name}</code>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Created:</span>
                                            <span className="font-semibold">
                                                {new Date(organization.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-medium">Address</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground">{organization.address || "No address provided"}</p>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        <TabsContent value="users" className="mt-4">
                            <div className="rounded-md border">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Full Name</TableHead>
                                            <TableHead>Email</TableHead>
                                            <TableHead>Role</TableHead>
                                            <TableHead>Status</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {usersLoading ? (
                                            <TableRow>
                                                <TableCell colSpan={4} className="text-center py-8">
                                                    Loading users...
                                                </TableCell>
                                            </TableRow>
                                        ) : usersData?.data.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={4} className="text-center py-8">
                                                    No users found for this organization.
                                                </TableCell>
                                            </TableRow>
                                        ) : (
                                            usersData?.data.map((user) => (
                                                <TableRow key={user.id}>
                                                    <TableCell className="font-medium">{user.full_name || "N/A"}</TableCell>
                                                    <TableCell>{user.email}</TableCell>
                                                    <TableCell>
                                                        <Badge variant="outline">
                                                            {user.is_superuser ? "Admin" : "User"}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Badge variant={user.is_active ? "success" : "destructive"}>
                                                            {user.is_active ? "Active" : "Inactive"}
                                                        </Badge>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </div>
                        </TabsContent>

                        <TabsContent value="license" className="mt-4">
                            <div className="space-y-4">
                                {licensesLoading ? (
                                    <div className="text-center py-8">Loading licenses...</div>
                                ) : licensesData?.data.length === 0 ? (
                                    <div className="text-center py-8 rounded-lg border border-dashed">
                                        No active license found for this organization.
                                    </div>
                                ) : (
                                    licensesData?.data.map((license) => (
                                        <Card key={license.id} className="overflow-hidden border-primary/20 shadow-sm">
                                            <div className="bg-primary/5 px-6 py-3 border-b border-primary/10 flex justify-between items-center">
                                                <div className="flex items-center gap-2">
                                                    <Key className="h-5 w-5 text-primary" />
                                                    <span className="font-bold uppercase tracking-tight">{license.tier} License</span>
                                                </div>
                                                <Badge variant={license.is_active ? "success" : "destructive"}>
                                                    {license.is_active ? "Active" : "Expired"}
                                                </Badge>
                                            </div>
                                            <CardContent className="p-6 grid gap-6 md:grid-cols-2">
                                                <div className="space-y-3">
                                                    <h4 className="text-xs font-bold uppercase text-muted-foreground tracking-widest">Details</h4>
                                                    <div className="space-y-1 text-sm">
                                                        <div className="flex justify-between">
                                                            <span className="text-muted-foreground">Key:</span>
                                                            <code className="bg-secondary px-1 rounded text-xs select-all cursor-pointer">{license.license_key}</code>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-muted-foreground">Valid From:</span>
                                                            <span className="font-medium">{new Date(license.valid_from).toLocaleDateString()}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-muted-foreground">Valid Until:</span>
                                                            <span className="font-medium">{new Date(license.valid_until).toLocaleDateString()}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="space-y-3">
                                                    <h4 className="text-xs font-bold uppercase text-muted-foreground tracking-widest">Quotas</h4>
                                                    <div className="grid grid-cols-3 gap-2">
                                                        <div className="bg-secondary/30 p-2 rounded-lg text-center">
                                                            <p className="text-[10px] text-muted-foreground uppercase">Users</p>
                                                            <p className="font-bold">{license.max_users}</p>
                                                        </div>
                                                        <div className="bg-secondary/30 p-2 rounded-lg text-center">
                                                            <p className="text-[10px] text-muted-foreground uppercase">Locations</p>
                                                            <p className="font-bold">{license.max_locations}</p>
                                                        </div>
                                                        <div className="bg-secondary/30 p-2 rounded-lg text-center">
                                                            <p className="text-[10px] text-muted-foreground uppercase">Devices</p>
                                                            <p className="font-bold">{license.max_devices}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))
                                )}
                            </div>
                        </TabsContent>
                    </Tabs>
                </DialogContent>
            </Dialog>
        </>
    )
}

export default OrganizationDetails
