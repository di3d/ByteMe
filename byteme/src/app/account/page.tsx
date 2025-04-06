// app/account/page.tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { getAuth } from "firebase/auth"
import { toast } from "sonner" // Updated import

// Form schema validation
const accountFormSchema = z.object({
  email: z.string().email("Invalid email address").optional(),
  phone: z.string().min(10, "Phone number too short").max(15),
  address: z.string().min(5, "Address too short"),
})

type AccountFormValues = z.infer<typeof accountFormSchema>

export default function AccountPage() {
  const auth = getAuth()
  
  // Mock current user data
  const currentUser = {
    email: auth.currentUser?.email || "",
    phone: "+1 (555) 123-4567",
    address: "123 Tech Street, Silicon Valley",
  }

  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountFormSchema),
    defaultValues: {
      email: currentUser.email,
      phone: currentUser.phone,
      address: currentUser.address,
    },
  })

  async function onSubmit(data: AccountFormValues) {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.success("Profile updated successfully") // Sonner toast
    } catch (error) {
      toast.error("Failed to update profile") // Error toast
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">My Account</h1>
          <p className="text-muted-foreground">
            Manage your contact information
          </p>
        </div>

        <Separator />

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="your@email.com" 
                      {...field} 
                      disabled 
                      className="opacity-70 cursor-not-allowed"
                    />
                  </FormControl>
                  <p className="text-sm text-muted-foreground">
                    Managed by Google Sign-In
                  </p>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone Number</FormLabel>
                  <FormControl>
                    <Input placeholder="+65 8123 4567" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Address</FormLabel>
                  <FormControl>
                    <Input placeholder="123 Main St, City, Country" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex justify-end">
              <Button 
                type="submit"
                disabled={form.formState.isSubmitting}
              >
                {form.formState.isSubmitting ? "Saving..." : "Update Profile"}
              </Button>
            </div>
          </form>
        </Form>

        <Separator />

        <div className="text-sm text-muted-foreground">
          <p>Signed in with Google as: {auth.currentUser?.email}</p>
        </div>
      </div>
    </div>
  )
}