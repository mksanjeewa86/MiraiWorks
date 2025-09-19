/**
 * Basic test to ensure Jest setup is working.
 */

describe('Basic Tests', () => {
  it('should run basic arithmetic test', () => {
    expect(2 + 2).toBe(4);
  });

  it('should work with strings', () => {
    expect('hello' + ' world').toBe('hello world');
  });

  it('should work with arrays', () => {
    const arr = [1, 2, 3];
    expect(arr).toHaveLength(3);
    expect(arr).toContain(2);
  });

  it('should work with objects', () => {
    const obj = { name: 'test', value: 42 };
    expect(obj).toHaveProperty('name', 'test');
    expect(obj.value).toBe(42);
  });
});

describe('API URL Validation', () => {
  it('should validate API endpoint format', () => {
    const apiUrl = 'http://localhost:8000';
    const endpoint = '/api/calendar/events';
    const fullUrl = `${apiUrl}${endpoint}`;

    expect(fullUrl).toBe('http://localhost:8000/api/calendar/events');
  });

  it('should handle datetime strings', () => {
    const dateString = '2025-01-15T09:00:00.000Z';
    const date = new Date('2025-01-15T09:00:00Z');

    expect(date.toISOString()).toBe(dateString);
  });
});