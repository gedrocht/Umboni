import { describe, expect, it } from 'vitest';

import { getHealthcheck } from '../src/index.js';

describe('getHealthcheck', () => {
  it('returns a normalized healthcheck for a valid service', () => {
    expect(getHealthcheck('  Umboni API  ')).toEqual({
      service: 'Umboni API',
      status: 'ok'
    });
  });

  it('throws for an empty service name', () => {
    expect(() => {
      getHealthcheck('   ');
    }).toThrowError('Service name is required.');
  });
});

