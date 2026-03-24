---
name: UI Development - Flights Search Simulator
description: |
  Instructions and guidelines to build a visual interface for the `flights_search` agent. 
  This UI takes structured user inputs and displays simulated flights list.
---

# 🛫 Skill: Developing the Flights Search Simulator UI

This skill enables the agent to design and implement a modern, premium frontend for the **Flights Search Agent**. The goal is to simulate a realistic search engine experience with glassmorphism aesthetics and smooth transitions.

---

## 🏗️ Architecture & Stack Choice

-   **Framework:** **Vite + React (JavaScript)** — Selected for modular component architecture and fast development.
-   **Styling:** **Vanilla CSS** with CSS Variables (Theme tokens). No Tailwind unless requested.
-   **State Management:** React Hooks (`useState`, `useEffect`).
-   **API Integration:** Standard `fetch` API to `http://127.0.0.1:8000/run-flights-search`.

---

## 📐 UI/UX Design Specifications

### 🌿 Aesthetic Guidelines
-   **Vibe:** Premium, modern, airy (Glassmorphism).
-   **Palette:**
    -   Deep Ocean / Midnight Backgrounds (Sleek dark mode).
    -   Soft neon accent lights (Gradients).
-   **Typography:** Google Fonts (Inter, Roboto, or Outfitters).

### 🖥️ Page Layout (Single Screen App)
1.  **Header:** Clean navigation with branding.
2.  **Search Bar (The Input):**
    -   Fields: `Origin`, `Destination`, `Departure Date`, `Return Date`, `Passengers` (Drop-down).
    -   Subtle animations on hover/focus.
3.  **Results Section (The Output):**
    -   Cards displaying simulated flights.
    -   Details: Airline logo/name, Flight number, Dep/Arr times, Duration, Stops, Price.

---

## 🛠️ Step-by-Step Implementation Workflow

### Step 1: Initialize Project
Use `npx -y create-vite@latest` to bootstrap the app.
```bash
npx -y create-vite@latest frontend --template react
cd frontend
npm install
```

### Step 2: Define Theme Variables (`index.css`)
Create a robust styling system using CSS custom properties.
```css
:root {
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  --primary-glow: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  --text-primary: #ffffff;
}
```

### Step 3: Implement Search Form Component
Map inputs precisely to `FlightsSearchInput` schema.
-   Origin & Destination (City/Code inputs).
-   Dates (Modern HTML `<input type="date">` styled).
-   Passengers (Quantity counter).

### Step 4: Map Results to Layout
Iterate over `results[0].flights` from agents response.
-   Use descriptive CSS Grid for the Flight Card layout.

---

## 🧪 Verification Checklists

### 🔍 Automated Proofing
-   Ensure API endpoint ports are configurable (defaulting to `:8000`).
-   Verify responsive design (Mobile viewport tests).

### ✅ Manual Checklist
-   [ ] Inputs trigger correct payload sent to `/run-flights-search`.
-   [ ] Resulting page displays 15 flight cards as simulated by the agent.
-   [ ] Loader states are fluid during LLM latency.
