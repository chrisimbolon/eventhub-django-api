import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import EventsPage from "./pages/EventsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<div>Dashboard (coming soon)</div>} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/sessions" element={<div>Sessions Page</div>} />
          <Route path="/attendees" element={<div>Attendees Page</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
