/**
 * Component Style Variants
 * Predefined style variants for consistent component styling
 */

import { type VariantProps } from "class-variance-authority";
import { cva } from "class-variance-authority";

// Button variants
export const buttonVariants = cva(
  // Base styles
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        // Financial specific variants
        profit: "bg-green-600 text-white hover:bg-green-700",
        loss: "bg-red-600 text-white hover:bg-red-700",
        neutral: "bg-orange-600 text-white hover:bg-orange-700",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        xl: "h-12 rounded-lg px-10",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

// Card variants
export const cardVariants = cva(
  "rounded-lg border bg-card text-card-foreground shadow-sm",
  {
    variants: {
      variant: {
        default: "border-border",
        outline: "border-2 border-primary",
        ghost: "border-transparent shadow-none",
        elevated: "shadow-lg border-border/50",
        // Financial specific variants
        profit: "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950",
        loss: "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950",
        neutral: "border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950",
      },
      padding: {
        none: "p-0",
        sm: "p-3",
        default: "p-6",
        lg: "p-8",
      },
    },
    defaultVariants: {
      variant: "default",
      padding: "default",
    },
  }
);

// Badge variants
export const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary: "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive: "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        // Status variants
        success: "border-transparent bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
        warning: "border-transparent bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
        error: "border-transparent bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
        info: "border-transparent bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
        // Financial status variants
        processing: "border-transparent bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
        completed: "border-transparent bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
        failed: "border-transparent bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
        pending: "border-transparent bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

// Alert variants
export const alertVariants = cva(
  "relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground",
  {
    variants: {
      variant: {
        default: "bg-background text-foreground",
        destructive: "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
        success: "border-green-500/50 text-green-700 dark:border-green-500 dark:text-green-400 [&>svg]:text-green-600 dark:[&>svg]:text-green-400",
        warning: "border-orange-500/50 text-orange-700 dark:border-orange-500 dark:text-orange-400 [&>svg]:text-orange-600 dark:[&>svg]:text-orange-400",
        info: "border-blue-500/50 text-blue-700 dark:border-blue-500 dark:text-blue-400 [&>svg]:text-blue-600 dark:[&>svg]:text-blue-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

// Progress variants
export const progressVariants = cva(
  "relative h-4 w-full overflow-hidden rounded-full bg-secondary",
  {
    variants: {
      variant: {
        default: "[&>div]:bg-primary",
        success: "[&>div]:bg-green-600",
        warning: "[&>div]:bg-orange-600",
        error: "[&>div]:bg-red-600",
        info: "[&>div]:bg-blue-600",
      },
      size: {
        sm: "h-2",
        default: "h-4",
        lg: "h-6",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

// Input variants
export const inputVariants = cva(
  "flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "",
        error: "border-red-500 focus-visible:ring-red-500",
        success: "border-green-500 focus-visible:ring-green-500",
        warning: "border-orange-500 focus-visible:ring-orange-500",
      },
      size: {
        sm: "h-8 px-2 text-xs",
        default: "h-10",
        lg: "h-12 px-4 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

// Typography variants
export const typographyVariants = cva("", {
  variants: {
    variant: {
      h1: "scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl",
      h2: "scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight transition-colors first:mt-0",
      h3: "scroll-m-20 text-2xl font-semibold tracking-tight",
      h4: "scroll-m-20 text-xl font-semibold tracking-tight",
      h5: "scroll-m-20 text-lg font-semibold tracking-tight",
      h6: "scroll-m-20 text-base font-semibold tracking-tight",
      p: "leading-7 [&:not(:first-child)]:mt-6",
      blockquote: "mt-6 border-l-2 pl-6 italic",
      code: "relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold",
      lead: "text-xl text-muted-foreground",
      large: "text-lg font-semibold",
      small: "text-sm font-medium leading-none",
      muted: "text-sm text-muted-foreground",
    },
  },
  defaultVariants: {
    variant: "p",
  },
});

// Chat message variants
export const chatMessageVariants = cva(
  "max-w-[80%] rounded-lg px-4 py-2 text-sm",
  {
    variants: {
      role: {
        user: "ml-auto bg-primary text-primary-foreground",
        assistant: "mr-auto bg-muted text-muted-foreground",
        system: "mx-auto bg-secondary text-secondary-foreground text-center text-xs",
      },
      status: {
        sending: "opacity-70",
        sent: "opacity-100",
        error: "border border-red-500 bg-red-50 text-red-700",
      },
    },
    defaultVariants: {
      role: "user",
      status: "sent",
    },
  }
);

// File upload variants
export const fileUploadVariants = cva(
  "flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-colors",
  {
    variants: {
      state: {
        idle: "border-gray-300 bg-gray-50 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:hover:bg-gray-600",
        dragOver: "border-primary bg-primary/10",
        uploading: "border-orange-500 bg-orange-50",
        success: "border-green-500 bg-green-50",
        error: "border-red-500 bg-red-50",
      },
    },
    defaultVariants: {
      state: "idle",
    },
  }
);

// Export variant prop types for TypeScript
export type ButtonVariants = VariantProps<typeof buttonVariants>;
export type CardVariants = VariantProps<typeof cardVariants>;
export type BadgeVariants = VariantProps<typeof badgeVariants>;
export type AlertVariants = VariantProps<typeof alertVariants>;
export type ProgressVariants = VariantProps<typeof progressVariants>;
export type InputVariants = VariantProps<typeof inputVariants>;
export type TypographyVariants = VariantProps<typeof typographyVariants>;
export type ChatMessageVariants = VariantProps<typeof chatMessageVariants>;
export type FileUploadVariants = VariantProps<typeof fileUploadVariants>;
