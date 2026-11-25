# Voice capture fixes (not deployed)

The headless profile now uses an Atomik template threshold of 0.55 instead
of 0.20. This is a starting value, not an empirically calibrated score.
Existing Pi config.ini files are not changed automatically.

Smart Turn now uses Silero VAD through sherpa-onnx for speech detection.
This does not select SenseVoice or change the OpenAI transcription model.
Install the updated headless requirements and provide src/stt/silero_vad.onnx
before enabling voice. The model URL used by the original Install.sh is:
https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx
Do not run the full Install.sh just for this dependency.

Without speech VAD the shared recorder refuses to record instead of silently
falling back to volume-only detection. If Smart Turn is unavailable but Silero
is present, speech detection still works with the configured silence timeout.
Semantic input preserves pauses and is padded at the beginning to eight seconds.

Microphone reads have a one-second total wait budget. Capture discards failed
reads, honors cancellation and wall-clock deadlines, and counts only frames
classified as speech in Smart Turn mode. Each capture resets detector state.

Offline tests cover rejected impulses, quiet frames accepted by a stub VAD,
preserved pauses, left padding, missing models, failed reads, wall-clock
deadlines, silence, and consecutive turns. They do not measure the real Silero
model's accuracy, the user's microphone, or end-to-end Pi latency.

No service start/restart, live recording, API call, or Pi deployment was performed.
Deployment should preserve existing config and change only the wake threshold;
do not regenerate the whole config if it has been customized since setup.
