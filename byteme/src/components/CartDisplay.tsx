import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Define TypeScript types
type CartItem = {
  cart_id: string;
  customer_id: string;
  name: string;
  parts_list: number[];
  total_cost: number;
  // Removed timestamp from the type since we're not using it
};

type CartDisplayProps = {
  cart: CartItem;
};

export function CartDisplay({ cart }: CartDisplayProps) {
  return (
    <Card className="w-full max-w-md mb-4">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>{cart.name}</CardTitle>
            <p className="text-sm text-muted-foreground">
              Customer ID: {cart.customer_id.substring(0, 8)}...
            </p>
          </div>
          <Badge variant="outline" className="text-sm">
            ${cart.total_cost.toLocaleString()}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-2">
          <div>
            <h4 className="text-sm font-medium">Cart ID:</h4>
            <p className="text-sm text-muted-foreground break-all">
              {cart.cart_id}
            </p>
          </div>
          
          <div>
            <h4 className="text-sm font-medium">Parts List:</h4>
            <div className="flex flex-wrap gap-2 mt-1">
              {cart.parts_list.map((partId, index) => (
                <Badge key={index} variant="secondary">
                  #{partId}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Usage example component
type CartListProps = {
  carts: CartItem[];
};

export function CartList({ carts }: CartListProps) {
  return (
    <div className="space-y-4">
      {carts.map((cart) => (
        <CartDisplay key={cart.cart_id} cart={cart} />
      ))}
    </div>
  );
}