export interface IRoute {
  items?: [] | IRoute[];
  name?: string;
  layout?: string;
  icon?: JSX.Element | string;
  path?: string;
  secondary?: boolean | undefined;
}
export interface RoutesType {
  name: string;
  layout: string;
  icon: JSX.Element | string;
  path: string;
  secondary?: boolean | undefined;
}
