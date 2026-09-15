"use client";

import { Button, type ButtonProps } from "@/components/ui/button";

interface ConfirmButtonProps extends ButtonProps {
  message: string;
  onConfirm: () => void;
}

export function ConfirmButton({
  message,
  onConfirm,
  children,
  ...props
}: ConfirmButtonProps) {
  return (
    <Button
      {...props}
      onClick={() => {
        if (window.confirm(message)) onConfirm();
      }}
    >
      {children}
    </Button>
  );
}
