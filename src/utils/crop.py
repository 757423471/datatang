from skimage import io

# 1936*1456 => 752*448

def image_region(img, region):
	xmin, ymin, xmax, ymax = region
	if xmin == xmax or ymin == ymax:
		return
	if xmin > xmax:
		xmax, xmin = xmin, xmax
		print('xmax and xmin swapped')
	if ymin > ymax:
		ymax, ymin = ymin, ymax
		print('ymax and ymin swapped')
	if xmax > 1936:
		xmax = 1935
		print('xmax beyond region')
	if ymax > 1456:
		ymax = 1455
		print('ymax beyond region')
	return img[ymin:ymax, xmin:xmax]

	# return img[1456-ymax:1456-ymin, 1936-xmax:1936-xmin]


def crop(img_name, dst_name, region):
	img = io.imread(img_name)
	roi = image_region(img, region)
	io.imsave(dst_name, roi)

