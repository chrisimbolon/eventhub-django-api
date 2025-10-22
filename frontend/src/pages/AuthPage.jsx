 // src/pages/AuthPage.jsx

import React, { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { toast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function AuthPage() {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password_confirm: "",
    first_name: "",
    last_name: "",
    role: "attendee", // Add default role
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: "" });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!isLogin) {
      // Registration validation
      if (!form.first_name.trim()) {
        newErrors.first_name = "First name is required";
      }
      if (!form.last_name.trim()) {
        newErrors.last_name = "Last name is required";
      }
      if (!form.email.trim()) {
        newErrors.email = "Email is required";
      } else if (!/\S+@\S+\.\S+/.test(form.email)) {
        newErrors.email = "Email is invalid";
      }
      if (form.password.length < 8) {
        newErrors.password = "Password must be at least 8 characters";
      }
      if (form.password !== form.password_confirm) {
        newErrors.password_confirm = "Passwords don't match";
      }
    }

    if (!form.username.trim()) {
      newErrors.username = "Username is required";
    }
    if (!form.password.trim()) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast({ 
        title: "Validation Error", 
        description: "Please fix the errors in the form",
        variant: "destructive" 
      });
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      if (isLogin) {
        await login({ 
          username: form.username, 
          password: form.password 
        });
        toast({ 
          title: "Welcome back!", 
          description: "You've successfully signed in." 
        });
        navigate("/");
      } else {
        await register(form);
        toast({ 
          title: "Account created!", 
          description: "Welcome to EventHub 🎉" 
        });
        navigate("/");
      }
    } catch (error) {
      console.error("Auth error:", error);
      
      // Handle different error types
      if (error.response?.data) {
        const errorData = error.response.data;
        
        // Check for field-specific errors
        if (typeof errorData === 'object' && !errorData.detail) {
          setErrors(errorData);
          toast({
            title: "Validation Error",
            description: "Please check the form for errors",
            variant: "destructive",
          });
        } else {
          toast({
            title: "Authentication failed",
            description: errorData.detail || errorData.message || "Please try again",
            variant: "destructive",
          });
        }
      } else {
        toast({
          title: "Network Error",
          description: "Unable to connect to server. Please try again.",
          variant: "destructive",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <Card className="max-w-md w-full shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl text-center font-bold">
            {isLogin ? "Sign In" : "Create Account"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <>
                <div>
                  <label className="text-sm font-medium">First Name *</label>
                  <Input
                    type="text"
                    name="first_name"
                    value={form.first_name}
                    onChange={handleChange}
                    className={errors.first_name ? "border-red-500" : ""}
                  />
                  {errors.first_name && (
                    <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>
                  )}
                </div>

                <div>
                  <label className="text-sm font-medium">Last Name *</label>
                  <Input
                    type="text"
                    name="last_name"
                    value={form.last_name}
                    onChange={handleChange}
                    className={errors.last_name ? "border-red-500" : ""}
                  />
                  {errors.last_name && (
                    <p className="text-red-500 text-xs mt-1">{errors.last_name}</p>
                  )}
                </div>

                <div>
                  <label className="text-sm font-medium">Email *</label>
                  <Input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    className={errors.email ? "border-red-500" : ""}
                  />
                  {errors.email && (
                    <p className="text-red-500 text-xs mt-1">{errors.email}</p>
                  )}
                </div>

                {/* Role Selection */}
                <div>
                  <label className="text-sm font-medium">I want to *</label>
                  <div className="grid grid-cols-2 gap-3 mt-2">
                    <button
                      type="button"
                      onClick={() => setForm({ ...form, role: "attendee" })}
                      className={`p-3 border-2 rounded-lg text-center transition ${
                        form.role === "attendee"
                          ? "border-blue-600 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="text-2xl mb-1">👤</div>
                      <div className="text-sm font-semibold">Attend Events</div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setForm({ ...form, role: "organizer" })}
                      className={`p-3 border-2 rounded-lg text-center transition ${
                        form.role === "organizer"
                          ? "border-blue-600 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="text-2xl mb-1">🎯</div>
                      <div className="text-sm font-semibold">Organize Events</div>
                    </button>
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="text-sm font-medium">Username *</label>
              <Input
                type="text"
                name="username"
                value={form.username}
                onChange={handleChange}
                className={errors.username ? "border-red-500" : ""}
              />
              {errors.username && (
                <p className="text-red-500 text-xs mt-1">{errors.username}</p>
              )}
            </div>

            <div>
              <label className="text-sm font-medium">Password *</label>
              <Input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                className={errors.password ? "border-red-500" : ""}
              />
              {errors.password && (
                <p className="text-red-500 text-xs mt-1">{errors.password}</p>
              )}
              {!isLogin && (
                <p className="text-xs text-gray-500 mt-1">
                  Minimum 8 characters
                </p>
              )}
            </div>

            {!isLogin && (
              <div>
                <label className="text-sm font-medium">Confirm Password *</label>
                <Input
                  type="password"
                  name="password_confirm"
                  value={form.password_confirm}
                  onChange={handleChange}
                  className={errors.password_confirm ? "border-red-500" : ""}
                />
                {errors.password_confirm && (
                  <p className="text-red-500 text-xs mt-1">{errors.password_confirm}</p>
                )}
              </div>
            )}

            <Button type="submit" disabled={loading} className="w-full mt-4">
              {loading ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Please wait...
                </span>
              ) : (
                isLogin ? "Sign In" : "Create Account"
              )}
            </Button>
          </form>

          <p className="text-center text-sm mt-4">
            {isLogin ? (
              <>
                Don't have an account?{" "}
                <button
                  onClick={() => {
                    setIsLogin(false);
                    setErrors({});
                  }}
                  className="text-blue-600 hover:underline font-semibold"
                >
                  Register
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button
                  onClick={() => {
                    setIsLogin(true);
                    setErrors({});
                  }}
                  className="text-blue-600 hover:underline font-semibold"
                >
                  Sign in
                </button>
              </>
            )}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

