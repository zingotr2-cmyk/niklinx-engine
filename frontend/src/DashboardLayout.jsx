import Sidebar from "./components/Sidebar";
import Overview from "./Overview";

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-white">
      <Sidebar />
      <main className="pl-64 min-h-screen">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <Overview />
        </div>
      </main>
    </div>
  );
}
