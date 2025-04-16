// Authentication utilities for handling JWT tokens
export type User = {
    email: string
    password: string
    name?: string
  }
  
export type AuthResponse = {
access_token?: string
error?: string
}

export const logout = (): void => {
localStorage.removeItem("access_token")
localStorage.removeItem("isAuthenticated")
document.cookie = "isAuthenticated=; path=/; max-age=0"

if (typeof window !== "undefined") {
    window.location.href = "/login"
}
}

export const isAuthenticated = (): boolean => {
if (typeof window === "undefined") return false
return localStorage.getItem("isAuthenticated") === "true" && !!localStorage.getItem("access_token")
}

export const getToken = (): string | null => {
if (typeof window === "undefined") return null
return localStorage.getItem("access_token")
}
