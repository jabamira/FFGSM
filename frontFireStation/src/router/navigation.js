import { useRouter } from "vue-router";

export function useNavigation() {
  const router = useRouter();

  const NavigateAuth = () =>
    router.push({ path: "/auth", query: { mode: "login" } });

  const NavigateAuthSignUp = () =>
    router.push({ path: "/auth", query: { mode: "signup" } });

  const NavigateHome = () => router.push("/");
  const NavigateUser = () => router.push("/user");
  const NavigateUsers = () => router.push("/users");
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
  const NavigatePassengerCars = () => router.push("/passenger-cars");
  const NavigateFireTruckWaybill = (id) =>
    router.push(`/fire-truck-waybill/${id}`);
  const NavigatePassengerCarWaybill = (id) =>
    router.push(`/passenger-car-waybill/${id}`);
  const NavigateUIComponents = () => router.push("/ui-elements");
  const NavigateRoles = () => router.push("/roles");

  return {
    NavigateAuth,
    NavigateAuthSignUp,
    NavigateHome,
    NavigateUser,
    NavigateUsers,
    NavigatePolls,
    NavigateFuelReport,
    NavigateDrivers,
    NavigateFireTrucksList,
    NavigateFireTrucksWayBills,
    NavigateFireTrucksNorms,
    NavigateLightVehiclesList,
    NavigateLightVehiclesWayBills,
    NavigateLightVehiclesNorms,
    NavigatePassengerCars,
    NavigateFireTruckWaybill,
    NavigatePassengerCarWaybill,
    NavigateUIComponents,
    NavigateRoles,
  };
}
