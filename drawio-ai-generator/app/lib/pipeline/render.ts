import { DiagramSchema } from "../schemas/diagram";
import { buildDrawioXml } from "../drawio/xml-builder";

export function renderDiagramXml(schema: DiagramSchema): string {
  return buildDrawioXml(schema);
}
