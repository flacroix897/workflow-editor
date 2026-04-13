import { Component, signal, ViewChild } from '@angular/core';
import { EllipseNode, RectangleNode } from '@relevance/workflow-editor';
import { DiagramEditorComponent } from '@relevance/workflow-editor/angular';

@Component({
  selector: 'app-root',
  imports: [DiagramEditorComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  @ViewChild(DiagramEditorComponent, { static: true }) editor!: DiagramEditorComponent;

  protected readonly title = signal('workflow-editor-angular-demo');

  async ngAfterViewInit() {
    this.editor.registerBuiltInNodes();

    const start = await this.editor.addNode(new EllipseNode({ label: 'START' }));
    const process = await this.editor.addNode(new RectangleNode({ label: 'PROCESS' }));

    start.connectTo(process);
  }
}
