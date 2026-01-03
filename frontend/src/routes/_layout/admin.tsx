import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { UsersService } from "@/client"

export const Route = createFileRoute("/_layout/admin")({
  component: AdminLayout,
  beforeLoad: async ({ context }) => {
    const queryClient = context.queryClient
    try {
      const user = await queryClient.ensureQueryData({
        queryKey: ["currentUser"],
        queryFn: UsersService.readUserMe,
      })
      if (!user.is_superuser) {
        throw redirect({
          to: "/",
        })
      }
    } catch (e) {
      throw redirect({
        to: "/login",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Admin - ControlAI",
      },
    ],
  }),
})

function AdminLayout() {
  return <Outlet />
}

export default AdminLayout
