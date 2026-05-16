import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Overview from "./Overview";
import ProductResearch from "./ProductResearch";
import StoreInsights from "./StoreInsights";
import MediaStudio from "./MediaStudio";
import SettingsPage from "./SettingsPage";
import ToastContainer from "./components/Toast";

export default function DashboardLayout() {
  const [view, setView] = useState("overview");

  const renderView = () => {
    switch (view) {
      case "research": return <ProductResearch />;
      case "store": return <StoreInsights />;
      case "media": return <MediaStudio />;
      case "settings": return <SettingsPage />;
      default: return <Overview onNavigate={setView} />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Sidebar activeView={view} onNavigate={setView} />
      <ToastContainer />
      <main className="pl-64 min-h-screen">
        <div className="max-w-6xl mx-auto px-8 py-8">
          {renderView()}
        </div>
      </main>
    </div>
  );
}
