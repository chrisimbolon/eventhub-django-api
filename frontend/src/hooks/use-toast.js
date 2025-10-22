let listeners = [];

export function toast(message, type = "default") {
  listeners.forEach((listener) => listener({ message, type }));
}

export function useToast() {
  const subscribe = (callback) => {
    listeners.push(callback);
    return () => {
      listeners = listeners.filter((l) => l !== callback);
    };
  };

  return { toast, subscribe };
}
