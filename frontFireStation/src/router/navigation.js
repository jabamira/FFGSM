import { useRouter } from "vue-router";

export function useNavigation() {
  const router = useRouter();

  const NavigateAuth = () =>
    router.push({ path: "/auth", query: { mode: "login" } });

  const NavigateAuthSignUp = () =>
    router.push({ path: "/auth", query: { mode: "signup" } });

  const NavigateHome = () => router.push("/");
  const NavigateUser = () => router.push("/user");
  const NavigatePolls = () => router.push("/polls");
  const NavigateFuelReport = () => router.push("/fuel-report");

  return {
    NavigateAuth,
    NavigateAuthSignUp,
    NavigateHome,
    NavigateUser,
    NavigatePolls,
    NavigateFuelReport,
  };
}
