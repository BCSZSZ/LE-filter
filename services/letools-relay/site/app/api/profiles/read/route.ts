// The deployment copies relay.mjs into lib; keep the endpoint wrapper trivial.
import { handle } from "../../../../lib/relay.mjs";

export const POST = handle;
export const OPTIONS = handle;
