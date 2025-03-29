import glob
import os
from pathlib import Path

import tqdm
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

input_dir = Path(os.environ["INPUT_DIRECTORY"])

output_dir = Path(os.environ["OUTPUT_DIRECTORY"])
output_dir.mkdir(exist_ok=True)


def main():
    input_doc_paths = [Path(f) for f in glob.glob(f"{input_dir}/**/*.pdf", recursive=True)]
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["en"]
    # pipeline_options.generate_page_images = True

    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    for doc in tqdm.tqdm(input_doc_paths):
        outpath = output_dir / doc.relative_to(input_dir).with_suffix(".md")

        conv_result = doc_converter.convert(doc, raises_on_error=False)
        os.makedirs(outpath.parent, exist_ok=True)
        with outpath.open("w", encoding="utf-8") as fp:
            fp.write(conv_result.document.export_to_markdown())


if __name__ == "__main__":
    main()
