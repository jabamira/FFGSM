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
  const NavigateDrivers = () => router.push("/drivers");
  const NavigateFireTrucksList = () => router.push("/fire-trucks-list");
  const NavigateFireTrucksWayBills = () => router.push("/fire-trucks-waybills");
  const NavigateFireTrucksNorms = () => router.push("/fire-trucks-norms");
  const NavigateLightVehiclesList = () => router.push("/light-vehicles-list");
  const NavigateLightVehiclesWayBills = () =>
    router.push("/light-vehicles-waybills");
  const NavigateLightVehiclesNorms = () => router.push("/light-vehicles-norms");

  return {
    NavigateAuth,
    NavigateAuthSignUp,
    NavigateHome,
    NavigateUser,
    NavigatePolls,
    NavigateFuelReport,
    NavigateDrivers,
    NavigateFireTrucksList,
    NavigateFireTrucksWayBills,
    NavigateFireTrucksNorms,
    NavigateLightVehiclesList,
    NavigateLightVehiclesWayBills,
    NavigateLightVehiclesNorms,
  };
}
