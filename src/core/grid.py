"""中文表格组件（基于 st-aggrid）"""

from st_aggrid import AgGrid, GridOptionsBuilder

_LOCALE_TEXT = {
    # 列头菜单
    "sortAscending": "升序",
    "sortDescending": "降序",
    "unSort": "取消排序",
    "columns": "列",
    "filter": "筛选",
    "searchOoo": "搜索…",
    "noMatches": "无匹配",
    # 固定 / 隐藏
    "pinColumn": "固定列",
    "pinLeft": "固定在左",
    "pinRight": "固定在右",
    "noPin": "不固定",
    "hideColumn": "隐藏列",
    "autoSizeThisColumn": "自适应列宽",
    "autoSizeAllColumns": "自适应所有列",
    # 导出
    "copy": "复制",
    "copyWithHeaders": "含表头复制",
    "ctrlC": "Ctrl+C",
    "ctrlX": "Ctrl+X",
    "paste": "粘贴",
    "export": "导出",
    "csvExport": "导出 CSV",
    "excelExport": "导出 Excel",
    # 右键菜单
    "copyToClipboard": "复制到剪贴板",
    "addRow": "添加行",
    "deleteRow": "删除行",
    "clearFilter": "清除筛选",
    # 分页
    "page": "页",
    "more": "更多",
    "to": "至",
    "of": "共",
    "next": "下一页",
    "previous": "上一页",
    "first": "首页",
    "last": "末页",
    "totalRows": "总行数：",
    # 统计
    "avg": "平均",
    "min": "最小值",
    "max": "最大值",
    "sum": "总和",
    "count": "计数",
    "group": "分组",
    # 通用
    "loadingOoo": "加载中…",
    "noRowsToShow": "暂无数据",
    "blank": "空白",
    "notEqual": "不等于",
    "equals": "等于",
    "lessThan": "小于",
    "greaterThan": "大于",
    "lessThanOrEqual": "小于等于",
    "greaterThanOrEqual": "大于等于",
    "inRange": "范围",
    "contains": "包含",
    "notContains": "不包含",
    "startsWith": "开头是",
    "endsWith": "结尾是",
    "true": "是",
    "false": "否",
    "applyFilter": "确定",
    "clearFilter": "清除",
    "reset": "重置",
}


def st_ag(df, **kwargs):
    """
    中文版表格组件，用法与 st.dataframe 类似。

    参数
    ----
    df : pd.DataFrame
        要显示的数据
    use_container_width : bool
        是否撑满容器宽度（默认 True）
    height : int
        表格高度（默认自动）
    """
    use_container_width = kwargs.pop("use_container_width", True)
    height = kwargs.pop("height", None)
    # 是否显示行号
    show_index = not kwargs.pop("hide_index", False)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(
        localeText=_LOCALE_TEXT,
        enableCellTextSelection=True,
        ensureDomOrder=True,
    )
    # 启用排序
    gb.configure_default_column(
        sortable=True,
        filterable=False,
        resizable=True,
    )
    grid_options = gb.build()

    return AgGrid(
        df,
        gridOptions=grid_options,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True if use_container_width else False,
        height=height,
        # 隐藏 row 点击高亮（纯展示）
        highlight_selected_on_render=False,
        theme="streamlit",
        **kwargs,
    )
