import { apiClient } from '@/api/client';
import type { PaginatedResponse } from '@/types';
import type {
  Category,
  CategoryPayload,
  SubTask,
  SubTaskPayload,
  Task,
  TaskFilters,
  TaskPayload,
  TaskSuggestion,
  TodaySummary,
} from '@/features/tasks/types';

/**
 * Tasks domain requests. Consumed exclusively via the TanStack Query hooks
 * in `features/tasks/hooks/` — no component calls these directly, per
 * ARCHITECTURE.md Section 2 ("No direct fetch calls inside components").
 */

export async function listTasksRequest(filters: TaskFilters): Promise<PaginatedResponse<Task>> {
  const { data } = await apiClient.get<PaginatedResponse<Task>>('/tasks/', { params: filters });
  return data;
}

export async function getTaskRequest(taskId: string): Promise<Task> {
  const { data } = await apiClient.get<Task>(`/tasks/${taskId}/`);
  return data;
}

export async function createTaskRequest(payload: TaskPayload): Promise<Task> {
  const { data } = await apiClient.post<Task>('/tasks/', payload);
  return data;
}

export async function updateTaskRequest(taskId: string, payload: TaskPayload): Promise<Task> {
  const { data } = await apiClient.patch<Task>(`/tasks/${taskId}/`, payload);
  return data;
}

export async function deleteTaskRequest(taskId: string): Promise<void> {
  await apiClient.delete(`/tasks/${taskId}/`);
}

export async function completeTaskRequest(taskId: string): Promise<Task> {
  const { data } = await apiClient.post<Task>(`/tasks/${taskId}/complete/`);
  return data;
}

export async function reopenTaskRequest(taskId: string): Promise<Task> {
  const { data } = await apiClient.post<Task>(`/tasks/${taskId}/reopen/`);
  return data;
}

export async function listCategoriesRequest(): Promise<Category[]> {
  const { data } = await apiClient.get<Category[]>('/tasks/categories/');
  return data;
}

export async function createCategoryRequest(payload: CategoryPayload): Promise<Category> {
  const { data } = await apiClient.post<Category>('/tasks/categories/', payload);
  return data;
}

export async function updateCategoryRequest(
  categoryId: string,
  payload: CategoryPayload
): Promise<Category> {
  const { data } = await apiClient.patch<Category>(`/tasks/categories/${categoryId}/`, payload);
  return data;
}

export async function deleteCategoryRequest(categoryId: string): Promise<void> {
  await apiClient.delete(`/tasks/categories/${categoryId}/`);
}

export async function listSubtasksRequest(taskId: string): Promise<SubTask[]> {
  const { data } = await apiClient.get<SubTask[]>(`/tasks/${taskId}/subtasks/`);
  return data;
}

export async function createSubtaskRequest(
  taskId: string,
  payload: SubTaskPayload
): Promise<SubTask> {
  const { data } = await apiClient.post<SubTask>(`/tasks/${taskId}/subtasks/`, payload);
  return data;
}

export async function updateSubtaskRequest(
  taskId: string,
  subtaskId: string,
  payload: SubTaskPayload
): Promise<SubTask> {
  const { data } = await apiClient.patch<SubTask>(
    `/tasks/${taskId}/subtasks/${subtaskId}/`,
    payload
  );
  return data;
}

export async function deleteSubtaskRequest(taskId: string, subtaskId: string): Promise<void> {
  await apiClient.delete(`/tasks/${taskId}/subtasks/${subtaskId}/`);
}

export async function getTaskSuggestionsRequest(): Promise<TaskSuggestion[]> {
  const { data } = await apiClient.get<TaskSuggestion[]>('/tasks/suggestions/');
  return data;
}

export async function getTodaySummaryRequest(): Promise<TodaySummary> {
  const { data } = await apiClient.get<TodaySummary>('/tasks/summary/today/');
  return data;
}
