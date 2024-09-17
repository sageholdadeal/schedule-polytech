from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from os import remove
from reportlab.lib import colors, styles
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from io import BytesIO


class Transformer:
	ARIAL_UNICODE = 'ArialUnicode'
	style_sheet = None

	def __init__(self, font_path: str):
		pdfmetrics.registerFont(ttfonts.TTFont(Transformer.ARIAL_UNICODE, font_path))

		self.style_sheet = styles.getSampleStyleSheet()
		self.style_sheet.add(
			styles.ParagraphStyle(name='BasicText', fontName=Transformer.ARIAL_UNICODE)  # TODO: make configurable
		)

	@staticmethod
	def _create_spans(span_ranges, rows_n, cols_n):
		spans = []
		for cell_range in span_ranges:
			bounds = cell_range.bounds
			if bounds[0] > cols_n or bounds[1] > rows_n:
				continue
			bounds = [bounds[:2], bounds[2:]]
			bounds = [(min(c - 1, cols_n - 1), min(r - 1, rows_n - 1)) for c, r in bounds]
			spans.append(('SPAN', bounds[0], bounds[1]))
		return spans

	def _get_values_from_sheet(self, ws, rows_n, cols_n):
		rows = []
		for r in range(1, rows_n + 1):
			values = []
			for c in range(1, cols_n + 1):
				cell = ws.cell(row=r, column=c)
				if type(cell) == MergedCell:
					values.append(None)
					continue

				cell_val = cell.value

				if type(cell_val) == str:
					cell_val = Paragraph('<para>%s</para>' % cell_val, self.style_sheet['BasicText'])

				values.append(cell_val)
			rows.append(values)
		return rows

	@staticmethod
	def _create_table(data, spans):
		table = Table(data)
		table.setStyle(TableStyle(spans + [
			('VALIGN', (0, 0), (-1, -1), 'TOP'),
			('GRID', (0, 0), (-1, -1), 1, colors.darkgrey),
		]))
		return table

	def transform(self, payload, rows_n, cols_n):
		ws = load_workbook(filename=BytesIO(payload)).active

		cols_n = cols_n if type(cols_n) == int else ws.max_column
		rows_n = rows_n if type(rows_n) == int else ws.max_row

		# TODO: don't save to file, let it in memory
		doc = SimpleDocTemplate('/tmp/xlsx2pdf_result.pdf')

		data = self._get_values_from_sheet(ws, rows_n, cols_n)

		spans = Transformer._create_spans(ws.merged_cells.ranges, rows_n, cols_n)

		elements = [Transformer._create_table(data, spans)]

		doc.build(elements)

		# TODO: hacking here
		f = open('/tmp/xlsx2pdf_result.pdf', 'rb')
		result = f.read()
		remove('/tmp/xlsx2pdf_result.pdf')
		return result
