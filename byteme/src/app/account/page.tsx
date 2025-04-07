"use client"

import { useEffect, useState } from "react"
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
import { toast } from "sonner"

// Form schema validation - remove email from the schema since it's disabled
const accountFormSchema = z.object({
  phone: z.string().min(10, "Phone number too short").max(15),
  address: z.string().min(5, "Address too short"),
})

type AccountFormValues = z.infer<typeof accountFormSchema>

export default function AccountPage() {
  const auth = getAuth();
  const [loading, setLoading] = useState(true);

  // State to hold customer data
  const [customerData, setCustomerData] = useState({
    phone: "",
    address: "Not provided",
  });

  // Fetch customer data from backend
  useEffect(() => {
    const fetchCustomerData = async () => {
      if (!auth.currentUser?.uid) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`http://localhost:5001/customer/${auth.currentUser.uid}`);
        const data = await response.json();

        if (data.code === 200) {
          setCustomerData({
            phone: data.data.phone || "",
            address: data.data.address || "Not provided",
          });
        }
      } catch (error) {
        console.error("Error fetching customer data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomerData();
  }, [auth.currentUser]);

  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountFormSchema),
    defaultValues: customerData,
  });

  // Update form when customer data changes
  useEffect(() => {
    form.reset(customerData);
  }, [customerData, form]);

  async function onSubmit(data: AccountFormValues) {
    try {
      // Submit data to backend
      const response = await fetch(`http://localhost:5001/customer/${auth.currentUser?.uid}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: auth.currentUser?.displayName || 'Unknown',
          address: data.address,
          // phone: data.phone,
          email: auth.currentUser?.email
        }),
      });

      const result = await response.json();

      if (result.code === 200 || result.code === 201) {
        toast.success("Profile updated successfully");
      } else {
        throw new Error(result.message || "Failed to update profile");
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      toast.error("Failed to update profile");
    }
  }

  if (loading) {
    return <div className="container mx-auto py-8">Loading your profile...</div>;
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

        {/* Email field outside the form */}
        <div className="space-y-2 mb-6">
          <label className="text-sm font-medium">Email</label>
          <Input
            value={auth.currentUser?.email || ""}
            disabled
            className="opacity-70 cursor-not-allowed"
          />
          <p className="text-sm text-muted-foreground">
            Managed by Google Sign-In
          </p>
        </div>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
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