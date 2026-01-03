import { Eye } from "lucide-react"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import type { LogPublic } from "@/client"
import { Badge } from "@/components/ui/badge"

interface LogDetailsProps {
    log: LogPublic
}

export const LogDetails = ({ log }: LogDetailsProps) => {
    const getLevelVariant = (level: string) => {
        switch (level) {
            case "error": return "destructive"
            case "warning": return "outline" // or a custom warning color if we had one
            case "success": return "default" // usually green in our theme
            default: return "secondary"
        }
    }

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon">
                    <Eye className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        Log Details
                        <Badge variant={getLevelVariant(log.level)}>{log.level}</Badge>
                    </DialogTitle>
                    <DialogDescription>
                        Detailed information for audit log entry.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <span className="font-bold text-sm">Timestamp:</span>
                        <span className="col-span-3 text-sm">{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <span className="font-bold text-sm">Action:</span>
                        <span className="col-span-3 text-sm">{log.action}</span>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <span className="font-bold text-sm">Target:</span>
                        <span className="col-span-3 text-sm">{log.target}</span>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <span className="font-bold text-sm">User ID:</span>
                        <span className="col-span-3 text-sm font-mono text-xs">{log.user_id || "System"}</span>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <span className="font-bold text-sm">IP Address:</span>
                        <span className="col-span-3 text-sm">{log.ip_address || "N/A"}</span>
                    </div>
                    <div className="flex flex-col gap-2 mt-2">
                        <span className="font-bold text-sm">Details:</span>
                        <div className="bg-muted p-3 rounded-md overflow-auto max-h-60">
                            <pre className="text-xs whitespace-pre-wrap break-all">
                                {log.details || "No additional details provided."}
                            </pre>
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}
