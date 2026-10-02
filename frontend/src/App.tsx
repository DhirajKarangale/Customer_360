import { Button } from "@/components/ui/button"

function App() {
  return (
    <>
      <div className="flex min-h-svh flex-col items-center justify-center">
        <Button>
          <span className="text-size-filters text-clr-danger">
            Click me
          </span>
        </Button>
      </div>
    </>
  )
}

export default App
