export class ApiError extends Error {
  constructor(message, { status = 0, inconclusive = false, chargedCalls = null } = {}) {
    super(message);
    this.status = status;
    this.inconclusive = inconclusive;
    this.chargedCalls = chargedCalls;
  }
}
