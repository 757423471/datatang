from settings import logger

class BoundingBoxError(Exception):
	"""
	return error code and message, meanwhile modified result if possible
	"""
	SERIOUS = 1
	WARNING = 2
	TRIVIAL = 3

	def __init__(self, code, message, recommend):
		super(BoundingBoxError, self).__init__()
		self.code = code
		self.message = message
		self.recommend = recommend

	def __str__(self):
		return self.message

# ensure x1 < x2 and y1 < y2
# while (x1, y1, x2, y2) = region
def normalize(region, width=1936, height=1456):
	xmin, ymin, xmax, ymax = region

	# no idea what the possible value is
	if xmin == xmax or ymin == ymax:
		raise BoundingBoxError(BoundingBoxError.SERIOUS, "across corners are overlapped", None)
	if xmin > width or ymin > height:
		raise BoundingBoxError(BoundingBoxError.SERIOUS, "bounding box makes no sense", None)
	
	msgs = []
	# maybe we shall not pass the boundray?
	if xmax > width:
		xmax = width - 1
		msgs.append("horizontal bar of bounding box is outside the boundary")
	if ymax > height:
		ymax = height - 1
		msgs.append("vertical bar of bounding box is outside the boundary")

	if msgs:
		raise BoundingBoxError(BoundingBoxError.WARNING, '; '.join(msgs), (xmin, ymin, width, ymax))
	
	# common cases, just flip
	if xmin > xmax:
		xmax, xmin = xmin, xmax
		msgs.append("coordinate along x-axis is upside down")
	if ymin > ymax:
		ymax, ymin = ymin, ymax
		msgs.append("coordinate along y-axis is upside down")
	if msgs:
		raise BoundingBoxError(BoundingBoxError.TRIVIAL, '; '.join(msgs), (xmin, ymin, xmax, ymax))
	else:
		return (xmin, ymin, xmax, ymax)

# implemented in skimage may be not a good idea

# def crop(img_name, dst_name, region):
# 	from skimage import io
# 	img = io.imread(img_name)
# 	try:
# 		xmin, ymin, xmax, ymax = normalize(region)
# 	except BoundingBoxError as e:
# 		if e.code == BoundingBoxError.SERIOUS or e.code == BoundingBoxError.WARNING:
# 			logger.error("unable to crop {0} for {1}".format(img_name, e))
# 			return -1
# 		if e.code == BoundingBoxError.TRIVIAL:
# 			logger.warning("found error {1} for {0}, but cropped still".format(img_name, e))
# 			xmin, ymin, xmax, ymax = e.recommend
# 	roi = img[ymin:ymax, xmin:xmax]
# 	io.imsave(dst_name, roi)


def crop(img_name, dst_name, region):
	from PIL import Image
	im = Image.open(img_name)

	try:
		xmin, ymin, xmax, ymax = normalize(region, im.width, im.height)
	except BoundingBoxError as e:
		if e.code == BoundingBoxError.SERIOUS or e.code == BoundingBoxError.WARNING:
			logger.error("unable to crop {0} for {1}".format(img_name, e))
			return -1
		if e.code == BoundingBoxError.TRIVIAL:
			logger.warning("found error {1} for {0}, but cropped still".format(img_name, e))
			xmin, ymin, xmax, ymax = e.recommend
	
	region_im = im.crop((xmin, ymin, xmax, ymax))
	region_im.save(dst_name)


