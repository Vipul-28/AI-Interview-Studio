// WebSocket client service for real-time interview communication

const WS_BASE_URL = "ws://localhost:8000/interview/ws";

class InterviewWebSocketService {
  constructor() {
    this.ws = null;
    this.onMessageCallback = null;
    this.onErrorCallback = null;
    this.onCloseCallback = null;
  }

  connect(sessionId, { onMessage, onError, onClose }) {
    if (this.ws) {
      this.disconnect();
    }

    this.onMessageCallback = onMessage;
    this.onErrorCallback = onError;
    this.onCloseCallback = onClose;

    const url = `${WS_BASE_URL}/${sessionId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log(`WebSocket connected for session: ${sessionId}`);
    };

    this.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (this.onMessageCallback) {
          this.onMessageCallback(payload);
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (this.onErrorCallback) {
        this.onErrorCallback(error);
      }
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket connection closed:", event);
      if (this.onCloseCallback) {
        this.onCloseCallback(event);
      }
    };
  }

  send(payload) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    } else {
      console.warn("WebSocket is not open. ReadyState:", this.ws?.readyState);
    }
  }

  sendAnswer(answerText) {
    this.send({
      type: "ANSWER",
      answer: answerText,
    });
  }

  sendSkip() {
    this.send({
      type: "SKIP",
    });
  }

  sendEndInterview() {
    this.send({
      type: "END_INTERVIEW",
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const interviewWebSocket = new InterviewWebSocketService();
