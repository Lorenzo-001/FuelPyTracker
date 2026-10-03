import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { LogOut, Loader2 } from "lucide-react"

interface LogoutConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
  isLoading?: boolean
}

export function LogoutConfirmDialog({
  open,
  onOpenChange,
  onConfirm,
  isLoading = false,
}: LogoutConfirmDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-rose-400">
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <LogOut className="h-5 w-5" />
            </div>
            <span>Conferma Disconnessione</span>
          </DialogTitle>
          <DialogDescription className="text-sm pt-2">
            Sei sicuro di voler uscire dal tuo account? Per visualizzare nuovamente le tue informazioni personali e registrare nuovi dati dovrai effettuare l&apos;accesso.
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="gap-2 sm:space-x-2 pt-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Annulla
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={onConfirm}
            disabled={isLoading}
            className="gap-2"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <LogOut className="h-4 w-4" />
            )}
            <span>Disconnetti</span>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
