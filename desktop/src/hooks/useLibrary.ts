import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getLibrary, scanLibrary } from "../api";

export function useLibrary() {
  const queryClient = useQueryClient();

  const libraryQuery = useQuery({
    queryKey: ["library"],
    queryFn: getLibrary,
  });

  const scanMutation = useMutation({
    mutationFn: scanLibrary,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["library"] });
    },
  });

  return {
    library: libraryQuery.data || [],
    isLoading: libraryQuery.isLoading,
    scan: scanMutation.mutate,
    isScanning: scanMutation.isPending,
  };
}
