export type Detection = {
  detection_id: number;
  class_id: number;
  class_name: string;
  box: [number, number, number, number];
  confidence: number;
};
export type DetectionResult = {
  request_id: string;
  model_version: string;
  profile: string;
  image_width: number;
  image_height: number;
  detections: Detection[];
  visible_count: number;
  thresholds: { confidence: number; nms_iou: number };
  latency_ms: number;
  warnings: string[];
};
export type Sample = {
  image_id: string;
  image_url: string;
  overlay_url: string;
  density: string;
  truth_count: number;
};

const configured = import.meta.env.VITE_API_URL as string | undefined;
export const API_URL = configured?.replace(/\/$/, "") ?? "";
export const asset = (path: string) => `${API_URL}${path}`;

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(payload.detail ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const getJson = async <T,>(path: string): Promise<T> => parse(await fetch(`${API_URL}${path}`));

export async function detectImage(
  image: Blob,
  filename: string,
  confidence: number,
  nmsIou: number
): Promise<DetectionResult> {
  const body = new FormData();
  body.append("image", image, filename);
  return parse(
    await fetch(
      `${API_URL}/v1/detections?confidence=${confidence}&nms_iou=${nmsIou}`,
      { method: "POST", body }
    )
  );
}

export async function detectSample(
  sample: Sample,
  confidence: number,
  nmsIou: number
): Promise<DetectionResult> {
  const response = await fetch(asset(sample.image_url));
  if (!response.ok) throw new Error("The selected shelf scene could not be loaded.");
  return detectImage(await response.blob(), `${sample.image_id}.png`, confidence, nmsIou);
}
