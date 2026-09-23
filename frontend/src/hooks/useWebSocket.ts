"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { AgentWSMessage } from "@/lib/types";
import { MOCK_WS_TIMELINE } from "@/lib/mockData";

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

interface UseWebSocketOptions {
  rcaId?: string;
  autoConnect?: boolean;
  onMessage?: (msg: AgentWSMessage) => void;
}

export function useWebSocket({ rcaId, autoConnect = true, onMessage }: UseWebSocketOptions = {}) {
  const [messages, setMessages] = useState<AgentWSMessage[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const socketRef = useRef<WebSocket | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Connect to real backend WebSocket
  useEffect(() => {
    if (!autoConnect || !rcaId || isSimulating) return;

    let ws: WebSocket;
    try {
      ws = new WebSocket(`${WS_BASE_URL}/ws/rca/${rcaId}`);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log(`[GraphTriage WS] Connected to /ws/rca/${rcaId}`);
      };

      ws.onmessage = (event) => {
        try {
          const parsed: AgentWSMessage = JSON.parse(event.data);
          setMessages((prev) => [...prev, parsed]);
          setCurrentStep(parsed.data.step || 0);
          if (onMessage) onMessage(parsed);
        } catch (err) {
          console.error("[GraphTriage WS] Error parsing message:", err);
        }
      };

      ws.onerror = (err) => {
        console.warn("[GraphTriage WS] Connection error, switching to mock standby:", err);
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
      };
    } catch (e) {
      console.warn("[GraphTriage WS] Unable to construct WebSocket:", e);
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [rcaId, autoConnect, isSimulating, onMessage]);

  // Simulation playback for offline demo
  const startSimulation = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    setMessages([]);
    setIsSimulating(true);
    setCurrentStep(0);

    let index = 0;
    const interval = setInterval(() => {
      if (index < MOCK_WS_TIMELINE.length) {
        const nextMsg = MOCK_WS_TIMELINE[index];
        setMessages((prev) => [...prev, nextMsg]);
        setCurrentStep(nextMsg.data.step);
        if (onMessage) onMessage(nextMsg);
        index++;
      } else {
        clearInterval(interval);
        setIsSimulating(false);
      }
    }, 1200);

    timerRef.current = interval;
  }, [onMessage]);

  const reset = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    setMessages([]);
    setCurrentStep(0);
    setIsSimulating(false);
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  return {
    messages,
    isConnected,
    isSimulating,
    currentStep,
    latestMessage: messages.length > 0 ? messages[messages.length - 1] : null,
    startSimulation,
    reset,
  };
}
