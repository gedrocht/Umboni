export type HealthStatus = 'ok';

export type Healthcheck = {
  readonly service: string;
  readonly status: HealthStatus;
};

export const getHealthcheck = (service: string): Healthcheck => {
  const normalizedService = service.trim();

  if (normalizedService.length === 0) {
    throw new Error('Service name is required.');
  }

  return {
    service: normalizedService,
    status: 'ok'
  };
};

