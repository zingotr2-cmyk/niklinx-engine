import { ProductProvider } from "./context/ProductContext";
import DashboardLayout from "./DashboardLayout";

export default function App() {
  return (
    <ProductProvider>
      <DashboardLayout />
    </ProductProvider>
  );
}
