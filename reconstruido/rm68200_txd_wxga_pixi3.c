/*
 * rm68200_txd_wxga_pixi3 - panel de la Alcatel Pixi 3 (10) WiFi 8080
 *
 * Reconstruido por ingenieria inversa del kernel de fabrica vECF-0
 * (Linux 3.10.54, Pixi310_Wifi_Global_Release), no es codigo de Alcatel.
 * Funciones origen: lcm_get_params @0xc039cf18, lcm_init @0xc039d0d4,
 * lcm_suspend @0xc039d004, lcm_resume @0xc039d30c, tabla @0xc0b5e298.
 *
 * PENDIENTE DE VERIFICAR contra lcm_drv.h del arbol destino:
 *   - los dos campos escritos en los offsets 0x248 y 0x250 de LCM_PARAMS (=1)
 *   - que GPIO26/GPIO27 con el bit 0x80000000 sean los habilitadores de
 *     alimentacion del panel (asi los usa lcm_set_gpio_output)
 */
#include "lcm_drv.h"

#define FRAME_WIDTH   (800)
#define FRAME_HEIGHT  (1280)

#define GPIO_LCM_PWR_EN   (0x8000001b)	/* GPIO27 | 0x80000000 */
#define GPIO_LCM_PWR2_EN  (0x8000001a)	/* GPIO26 | 0x80000000 */
#define GPIO_LCM_RST      (0x53)	/* GPIO83 */

#define REGFLAG_DELAY         0xFEF
#define REGFLAG_END_OF_TABLE  0xFFF

static LCM_UTIL_FUNCS lcm_util;
#define MDELAY(n) (lcm_util.mdelay(n))
#define dsi_set_cmdq(pdata, queue_size, force_update) \
	lcm_util.dsi_set_cmdq(pdata, queue_size, force_update)

struct LCM_setting_table {
	unsigned cmd;
	unsigned char count;
	unsigned char para_list[64];
};

static struct LCM_setting_table lcm_initialization_setting[] = {
	{0xFE, 1, {0x0E} },
	{0x01, 1, {0x63} },
	{0xFE, 1, {0x00} },
	{0x11, 1, {0x00} },		/* sleep out */
	{REGFLAG_DELAY, 34, {} },
	{0x29, 1, {0x00} },		/* display on */
	{REGFLAG_DELAY, 180, {} },
	{REGFLAG_END_OF_TABLE, 0x00, {} },
};

static void lcm_get_params(LCM_PARAMS *params)
{
	memset(params, 0, sizeof(LCM_PARAMS));

	params->type   = LCM_TYPE_DSI;			/* 2 */
	params->width  = FRAME_WIDTH;
	params->height = FRAME_HEIGHT;

	params->dsi.mode     = BURST_VDO_MODE;		/* 3 */
	params->dsi.LANE_NUM = LCM_FOUR_LANE;		/* 4 */
	params->dsi.data_format.format = LCM_DSI_FORMAT_RGB888;	/* 2 */
	params->dsi.PS       = LCM_PACKED_PS_24BIT_RGB888;	/* 2 */

	params->dsi.vertical_sync_active   = 4;
	params->dsi.vertical_backporch     = 8;
	params->dsi.vertical_frontporch    = 8;
	params->dsi.vertical_active_line   = FRAME_HEIGHT;

	params->dsi.horizontal_sync_active  = 4;
	params->dsi.horizontal_backporch    = 132;
	params->dsi.horizontal_frontporch   = 24;
	params->dsi.horizontal_active_pixel = FRAME_WIDTH;

	params->dsi.PLL_CLOCK = 224;			/* MHz */
	/* offsets 0x248 y 0x250 = 1: por identificar (ver cabecera) */
}

static void lcm_init(void)
{
	lcm_set_gpio_output(GPIO_LCM_PWR_EN, 1);  MDELAY(5);
	lcm_set_gpio_output(GPIO_LCM_PWR2_EN, 1); MDELAY(5);
	lcm_set_gpio_output(GPIO_LCM_RST, 1);     MDELAY(5);
	lcm_set_gpio_output(GPIO_LCM_RST, 0);     MDELAY(10);
	lcm_set_gpio_output(GPIO_LCM_RST, 1);     MDELAY(20);
	push_table(lcm_initialization_setting,
		   sizeof(lcm_initialization_setting) / sizeof(struct LCM_setting_table), 1);
}

static void lcm_suspend(void)
{
	unsigned int data_array[16];

	data_array[0] = 0x00280500;	/* display off */
	dsi_set_cmdq(data_array, 1, 1);
	MDELAY(34);
	data_array[0] = 0x00100500;	/* sleep in */
	dsi_set_cmdq(data_array, 1, 1);
	MDELAY(180);
	lcm_set_gpio_output(GPIO_LCM_RST, 0);     MDELAY(15);
	lcm_set_gpio_output(GPIO_LCM_PWR2_EN, 0); MDELAY(5);
	lcm_set_gpio_output(GPIO_LCM_PWR_EN, 0);  MDELAY(10);
}

static void lcm_resume(void)
{
	lcm_init();	/* el original solo imprime trazas y llama a lcm_init */
}

static void lcm_set_util_funcs(const LCM_UTIL_FUNCS *util)
{
	memcpy(&lcm_util, util, sizeof(LCM_UTIL_FUNCS));
}

LCM_DRIVER rm68200_txd_wxga_pixi3_lcm_drv = {
	.name           = "rm68200_txd_wxga_pixi3",
	.set_util_funcs = lcm_set_util_funcs,
	.get_params     = lcm_get_params,
	.init           = lcm_init,
	.suspend        = lcm_suspend,
	.resume         = lcm_resume,
};
