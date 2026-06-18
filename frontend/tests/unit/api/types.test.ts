import { describe, it, expect } from 'vitest';
import { ApiError, TERMINAL_STATUSES } from '../../../src/api/types';

describe('TERMINAL_STATUSES', () => {
  it('contains succeeded, failed, timed_out, and cancelled', () => {
    expect(TERMINAL_STATUSES.has('succeeded')).toBe(true);
    expect(TERMINAL_STATUSES.has('failed')).toBe(true);
    expect(TERMINAL_STATUSES.has('timed_out')).toBe(true);
    expect(TERMINAL_STATUSES.has('cancelled')).toBe(true);
  });

  it('does not contain queued or running', () => {
    expect(TERMINAL_STATUSES.has('queued')).toBe(false);
    expect(TERMINAL_STATUSES.has('running')).toBe(false);
  });
});

describe('ApiError', () => {
  it('sets httpStatus, message, and name, and is an instance of Error', () => {
    const err = new ApiError(404, 'Not found');
    expect(err.httpStatus).toBe(404);
    expect(err.message).toBe('Not found');
    expect(err.name).toBe('ApiError');
    expect(err).toBeInstanceOf(Error);
  });

  describe('retryable', () => {
    it('returns true for httpStatus 0 (network error)', () => {
      expect(new ApiError(0, '').retryable).toBe(true);
    });

    it('returns true for httpStatus 503', () => {
      expect(new ApiError(503, '').retryable).toBe(true);
    });

    it('returns true for httpStatus 500', () => {
      expect(new ApiError(500, '').retryable).toBe(true);
    });

    it('returns true for httpStatus 502 (>=500, not 503)', () => {
      expect(new ApiError(502, '').retryable).toBe(true);
    });

    it('returns false for httpStatus 400', () => {
      expect(new ApiError(400, '').retryable).toBe(false);
    });

    it('returns false for httpStatus 404', () => {
      expect(new ApiError(404, '').retryable).toBe(false);
    });

    it('returns false for httpStatus 200', () => {
      expect(new ApiError(200, '').retryable).toBe(false);
    });
  });
});
