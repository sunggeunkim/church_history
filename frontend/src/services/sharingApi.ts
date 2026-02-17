import api from "./api";
import type { CreateShareLinkResponse } from "@/types";

export async function createShareLink(
  shareType: "achievement" | "quiz_result" | "progress",
  achievementId?: number,
  quizId?: number,
): Promise<CreateShareLinkResponse> {
  const payload: Record<string, unknown> = { share_type: shareType };
  if (achievementId !== undefined) payload.achievement_id = achievementId;
  if (quizId !== undefined) payload.quiz_id = quizId;

  const response = await api.post<CreateShareLinkResponse>(
    "/sharing/links/",
    payload,
  );
  return response.data;
}

export async function deleteShareLink(token: string): Promise<void> {
  await api.delete(`/sharing/links/${token}/`);
}
