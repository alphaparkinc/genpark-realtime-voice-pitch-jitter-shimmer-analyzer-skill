import sys, json
from client import RealtimeVoicePitchJitterShimmerAnalyzerClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    analyzer = RealtimeVoicePitchJitterShimmerAnalyzerClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-realtime-voice-pitch-jitter-shimmer-analyzer-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    samples = req.get("samples", [0] * 640)
    res = analyzer.analyze_vocal_biomarkers(samples)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
